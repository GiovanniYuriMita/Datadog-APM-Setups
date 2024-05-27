#include <microhttpd.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include "trace_wrapper.h"

#define PORT 8888

const char *html_page_path = "index.html";

int serve_file(const char *path, struct MHD_Connection *connection) {
    FILE *file = fopen(path, "rb");
    if (!file) {
        perror("Error opening HTML file");
        return MHD_NO;
    }

    fseek(file, 0, SEEK_END);
    size_t file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *file_content = (char *)malloc(file_size + 1);
    if (!file_content) {
        perror("Error allocating memory for HTML file content");
        fclose(file);
        return MHD_NO;
    }

    fread(file_content, 1, file_size, file);
    file_content[file_size] = '\0'; // Null-terminate the file content
    fclose(file);

    struct MHD_Response *response = MHD_create_response_from_buffer(file_size, file_content, MHD_RESPMEM_MUST_FREE);
    int ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response);

    return ret;
}

void traced_function(void *arg) {
    printf("Traced Function Log %s\n", dd_logs_injection());
    // printf("Traced Function Log");
    sleep(1);
    dd_span_tag("additional_tag", "abc");
    dd_span_tag_int("int_tag", 456);
    dd_span_tag_float("float_tag", 789.01f);
}

int handle_request(void *cls, struct MHD_Connection *connection,
                   const char *url, const char *method, const char *version,
                   const char *upload_data, size_t *upload_data_size, void **con_cls) {
    printf("Received request: %s %s\n", method, url);

    if (strcmp(url, "/") == 0 && strcmp(method, "GET") == 0) {
        printf("Serving HTML page\n");
        return serve_file(html_page_path, connection);
    } else if (strcmp(url, "/trace") == 0 && strcmp(method, "GET") == 0) {
        printf("Received /trace request\n");

        // Setting Span Tags
        const char *const tags[][2] = {
            {"endpoint", "app.datadoghq.com"},
            {"tag2", "value2"},
            {"abc", "123"},
            {"teste", "testeabc"}
        };
        size_t num_tags = sizeof(tags) / sizeof(tags[0]);

        // Tracing a function
        dd_trace_function("handle_request", "/trace", tags, num_tags, traced_function, NULL); // Trace Function

        const char *response_str = "Traced C Function Executed";
        struct MHD_Response *response = MHD_create_response_from_buffer(strlen(response_str), (void *)response_str, MHD_RESPMEM_PERSISTENT);
        int ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
        MHD_destroy_response(response);

        return ret;
    } else {
        printf("Unknown request\n");
        const char *page = "<html><body>404 Not Found</body></html>";
        struct MHD_Response *response = MHD_create_response_from_buffer(strlen(page), (void *)page, MHD_RESPMEM_PERSISTENT);
        int ret = MHD_queue_response(connection, MHD_HTTP_NOT_FOUND, response);
        MHD_destroy_response(response);
        return ret;
    }
}

int main() {
    setbuf(stdout, NULL);

    init_tracer(); // ****

    struct MHD_Daemon *daemon;

    printf("Starting server...\n");
    daemon = MHD_start_daemon(MHD_USE_INTERNAL_POLLING_THREAD, PORT, NULL, NULL, &handle_request, NULL, MHD_OPTION_END);
    if (NULL == daemon) {
        fprintf(stderr, "Failed to start server: %s\n", strerror(errno));
        return 1;
    }

    printf("Server running on port %d\n", PORT);

    while (1) {
        sleep(10);
    }

    MHD_stop_daemon(daemon);
    return 0;
}
