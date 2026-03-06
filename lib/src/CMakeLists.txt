# 1. Include directories
set(PROJECT_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
)

# External header paths (compile-time only, no linking)
# These come from vcpkg's imported targets — we extract just the include dirs
set(VCPKG_INCLUDE_DIR "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/include")

# 2. Internal Static Libraries
add_library(utils STATIC core/utils.cc)
target_include_directories(utils PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(utils PRIVATE ${VCPKG_INCLUDE_DIR})

add_library(constants STATIC core/constants.cc)
target_include_directories(constants PUBLIC ${PROJECT_INCLUDE_DIRS})

add_library(operators STATIC core/operators.cc)
target_include_directories(operators PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(operators PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(operators PRIVATE constants)

add_library(chunk_obj STATIC s3vl/chunk_obj.cc)
target_include_directories(chunk_obj PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(chunk_obj PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(chunk_obj PRIVATE operators utils)

add_library(dataset_obj STATIC s3vl/dataset_obj.cc)
target_include_directories(dataset_obj PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(dataset_obj PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(dataset_obj PRIVATE chunk_obj)

add_library(file_callbacks STATIC s3vl/file_callbacks.cc)
target_include_directories(file_callbacks PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(file_callbacks PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(file_callbacks PRIVATE operators)

add_library(dataset_callbacks STATIC s3vl/dataset_callbacks.cc)
target_include_directories(dataset_callbacks PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(dataset_callbacks PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(dataset_callbacks PRIVATE file_callbacks dataset_obj)

add_library(group_callbacks STATIC s3vl/group_callbacks.cc)
target_include_directories(group_callbacks PUBLIC ${PROJECT_INCLUDE_DIRS})
target_include_directories(group_callbacks PRIVATE ${VCPKG_INCLUDE_DIR})
target_link_libraries(group_callbacks PRIVATE dataset_callbacks)

# 3. The Final VOL Connector (shared library)
#    ALL external deps linked ONLY here — single link, no duplicates
add_library(arraymorph SHARED s3vl/vol_connector.cc)
set_target_properties(arraymorph PROPERTIES PREFIX "lib")
target_include_directories(arraymorph PUBLIC ${PROJECT_INCLUDE_DIRS})
target_link_libraries(arraymorph PUBLIC
    group_callbacks
    ${ALL_DEPS}
)

# 4. Install
install(TARGETS arraymorph
    LIBRARY DESTINATION arraymorph/lib
    RUNTIME DESTINATION arraymorph/lib
)
