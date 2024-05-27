#ifndef TRACE_WRAPPER_H
#define TRACE_WRAPPER_H

#ifdef __cplusplus
extern "C" {
#endif

void init_tracer();
void dd_trace(const char *span_name, const char *resource_name, const char *const span_tags[][2], size_t num_tags);
void dd_trace_function(const char *span_name, const char *resource_name, const char *const span_tags[][2], size_t num_tags, void (*func)(void *), void *arg);
void dd_span_tag(const char *key, const char *value);
void dd_span_tag_int(const char *key, int value);
void dd_span_tag_float(const char *key, float value);
const char* dd_logs_injection();

#ifdef __cplusplus
}
#endif

#endif
