cmake_minimum_required(VERSION 3.10)
project(C_Datadog_APM)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)

# Include directories for Datadog, OpenTracing, and microhttpd
include_directories(${PROJECT_SOURCE_DIR}/include /usr/local/include /opt/opentracing-cpp/include)

# Link directories for Datadog, OpenTracing, and microhttpd
link_directories(/usr/local/lib /opt/opentracing-cpp/lib)

# Add the executable
add_executable(server src/main.c src/trace_wrapper.cpp)

# Link against Datadog, OpenTracing, microhttpd, and other required libraries
target_link_libraries(server dd_opentracing opentracing microhttpd curl ssl crypto z)
