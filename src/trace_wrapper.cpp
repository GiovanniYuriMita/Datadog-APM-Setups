#include <datadog/opentracing.h>
#include "trace_wrapper.h"
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <optional>

using namespace datadog::opentracing;
using namespace opentracing;

// ---------------------- >> Starting Current Span Definition >> ---------------------- //

namespace {
    // A thread-local variable to keep track of the current span
    thread_local std::unique_ptr<Span> current_span;
    thread_local std::string current_log_injection; // For storing log injection data

    // Helper function to start a new span and set it as the current span
    std::unique_ptr<opentracing::Span> start_span(const char *span_name) {
        auto parent_span = current_span.get();
        std::unique_ptr<opentracing::Span> span;
        if (parent_span) {
            span = Tracer::Global()->StartSpan(span_name, {ChildOf(&parent_span->context())});
        } else {
            span = Tracer::Global()->StartSpan(span_name);
        }

        // Get trace ID and span ID
        auto trace_id = span->context().ToTraceID();
        auto span_id = span->context().ToSpanID();

        // Store trace ID and span ID for log injection
        current_log_injection = "trace_id=" + trace_id + " span_id=" + span_id;

        return span;
    }
}
// ---------------------- >> Ending Current Span Definition >> ---------------------- //

// ---------------------- >> Starting Initialize the tracer globally >> ---------------------- //  
void init_tracer() {
    auto options = TracerOptions{};
    options.service = "bw-c"; // Service Name
    options.environment = "chofs"; // Env
    options.version = "1.0.0"; // Service Version
    // Sending Traces to Another Container
    options.agent_host = "datadog-agent";
    options.agent_port = 8126; 

    auto tracer = makeTracer(options);
    if (!tracer) {
        std::cerr << "Failed to create tracer\n";
        return;
    }
    std::cout << "Tracer created successfully\n";

    // Set the global tracer
    Tracer::InitGlobal(std::move(tracer));
    std::cout << "Global tracer set\n";
}
// ---------------------- >> Starting Initialize the tracer globally >> ---------------------- //

// ---------------------- >> Starting Span Creation Session >> ---------------------- //  
// Create a span
void dd_trace(const char *span_name, const char *resource_name, const char *const span_tags[][2], size_t num_tags) {
    auto span = Tracer::Global()->StartSpan(span_name);
    span->SetTag("language", "c");
    span->SetTag("resource.name", resource_name);

    for (size_t i = 0; i < num_tags; ++i) {
        span->SetTag(span_tags[i][0], span_tags[i][1]);
    }

    span->Finish();
}

// Trace a function
void dd_trace_function(const char *span_name, const char *resource_name, const char *const span_tags[][2], size_t num_tags, void (*func)(void *), void *arg) {
    auto span = start_span(span_name);
    span->SetTag("language", "c");
    span->SetTag("resource.name", resource_name);

    // Handling Span Tags
    for (size_t i = 0; i < num_tags; ++i) {
        span->SetTag(span_tags[i][0], span_tags[i][1]);
    }

    // Set the current span
    current_span = std::move(span);

    func(arg);  // Execute the function

    // Finish the span and clear the current span
    current_span->Finish();
    current_span.reset();
}
// ---------------------- >> Ending Span Creation Session >> ---------------------- //  

// ---------------------- >> Starting Span Tags Session >> ---------------------- //  
void dd_span_tag(const char *key, const char *value) {
    if (current_span) {
        current_span->SetTag(key, value);
    }
}

void dd_span_tag_int(const char *key, int value) {
    if (current_span) {
        current_span->SetTag(key, value);
    }
}

void dd_span_tag_float(const char *key, float value) {
    if (current_span) {
        current_span->SetTag(key, value);
    }
}

// ---------------------- >> Ending Span Tags Session >> ---------------------- //  

// ---------------------- >> Starting Trace && Span IDs retrieval >> ---------------------- //
const char* dd_logs_injection() {
    if (current_span) {
        return current_log_injection.c_str();
    }
    return "";
}
// Sample usage: printf("Log Something %s\n", dd_logs_injection().c_str());

// ---------------------- >> Ending Trace && Span IDs retrieval >> ---------------------- //
