cmake_minimum_required(VERSION 3.16)
project(pqc_lab_c_demos VERSION 0.1.0 LANGUAGES C)

# Set C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_C_FLAGS_DEBUG "-g -O0 -Wall -Wextra -DDEBUG")
set(CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG")

# Find liboqs
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBOQS REQUIRED liboqs)

# Include directories
include_directories(${LIBOQS_INCLUDE_DIRS})

# Link directories
link_directories(${LIBOQS_LIBRARY_DIRS})

# Add compile definitions
add_definitions(${LIBOQS_CFLAGS_OTHER})

# Find OpenSSL (optional, for enhanced functionality)
find_package(OpenSSL)
if(OpenSSL_FOUND)
    add_definitions(-DOQS_USE_OPENSSL=1)
    message(STATUS "OpenSSL found, enabling enhanced functionality")
else()
    message(STATUS "OpenSSL not found, using basic liboqs functionality")
endif()

# Common source files and libraries
set(COMMON_LIBS ${LIBOQS_LIBRARIES})
if(OpenSSL_FOUND)
    list(APPEND COMMON_LIBS OpenSSL::SSL OpenSSL::Crypto)
endif()

# KEM Demo
add_executable(kem_demo kem_demo/kem_demo.c)
target_link_libraries(kem_demo ${COMMON_LIBS})
target_compile_definitions(kem_demo PRIVATE -DKEM_DEMO)

# DSA Demo  
add_executable(dsa_demo dsa_demo/dsa_demo.c)
target_link_libraries(dsa_demo ${COMMON_LIBS})
target_compile_definitions(dsa_demo PRIVATE -DDSA_DEMO)

# Set RPATH for shared library loading
if(UNIX AND NOT APPLE)
    set_target_properties(kem_demo dsa_demo PROPERTIES
        INSTALL_RPATH "${LIBOQS_LIBRARY_DIRS}"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
endif()

# Installation
install(TARGETS kem_demo dsa_demo
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Install headers if needed
# install(FILES kem_demo/kem_demo.h dsa_demo/dsa_demo.h
#     DESTINATION include/pqc_lab
# )

# Testing
enable_testing()

# Add tests
add_test(NAME kem_demo_test COMMAND kem_demo)
add_test(NAME dsa_demo_test COMMAND dsa_demo)

# Set test properties
set_tests_properties(kem_demo_test dsa_demo_test PROPERTIES
    TIMEOUT 30
    ENVIRONMENT "LD_LIBRARY_PATH=${LIBOQS_LIBRARY_DIRS}"
)

# Print configuration summary
message(STATUS "PQC Lab C Demos Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C compiler: ${CMAKE_C_COMPILER}")
message(STATUS "  liboqs version: ${LIBOQS_VERSION}")
message(STATUS "  liboqs include dirs: ${LIBOQS_INCLUDE_DIRS}")
message(STATUS "  liboqs library dirs: ${LIBOQS_LIBRARY_DIRS}")
message(STATUS "  liboqs libraries: ${LIBOQS_LIBRARIES}")
message(STATUS "  OpenSSL: ${OpenSSL_FOUND}")
if(OpenSSL_FOUND)
    message(STATUS "  OpenSSL version: ${OpenSSL_VERSION}")
endif()
