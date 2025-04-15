set(SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/**.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/include/**.h
)

# format / tidy code
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_custom_target(format
    COMMAND
    clang-format
    -i
    -style=file:${CMAKE_CURRENT_SOURCE_DIR}/.clang-format
    ${SOURCES}
    COMMENT "Runing clang-format on source files"
)
add_custom_target(tidy
    COMMAND
    clang-tidy
    -p=${CMAKE_BINARY_DIR}
    ${SOURCES}
    COMMENT "Runing clang-tidy on source files"
)

# setup libraries
add_library(frontend STATIC src/select_keeb.cc)
target_include_directories(frontend INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)

# build executable
add_executable(${PROJECT_NAME} main.cc)
add_dependencies(${PROJECT_NAME} format tidy)
target_link_libraries(${PROJECT_NAME} frontend)
