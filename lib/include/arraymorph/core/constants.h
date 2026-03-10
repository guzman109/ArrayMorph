#ifndef __CONSTANTS__
#define __CONSTANTS__

#include <cstdlib>
#include <string>
#include <vector>

#define LOG_ENABLE
// #define PROFILE_ENABLE
#define ARRAYMORPH_SUCCESS 0
#define ARRAYMORPH_FAIL -1
#define FILL_VALUE 0
#define PROCESS
#define POOLEXECUTOR

// Read an integer env var, returning `fallback` if unset or invalid.
inline int envInt(const char *name, int fallback) {
  const char *val = std::getenv(name);
  if (!val) return fallback;
  char *end;
  long v = std::strtol(val, &end, 10);
  return (end != val && *end == '\0') ? static_cast<int>(v) : fallback;
}

// All tunables: set via env var or fall back to compile-time default.
//   ARRAYMORPH_S3_CONNECTIONS     (default 256)
//   ARRAYMORPH_REQUEST_TIMEOUT_MS (default 30000)
//   ARRAYMORPH_CONNECT_TIMEOUT_MS (default 30000)
//   ARRAYMORPH_POOL_SIZE          (default 8192)
//   ARRAYMORPH_RETRIES            (default 3)
//   ARRAYMORPH_THREAD_NUM         (default 256)
inline const int s3Connections    = envInt("ARRAYMORPH_S3_CONNECTIONS",     256);
inline const int requestTimeoutMs = envInt("ARRAYMORPH_REQUEST_TIMEOUT_MS", 30000);
inline const int connectTimeoutMs = envInt("ARRAYMORPH_CONNECT_TIMEOUT_MS", 30000);
inline const int poolSize         = envInt("ARRAYMORPH_POOL_SIZE",          8192);
inline const int retries          = envInt("ARRAYMORPH_RETRIES",            3);
inline const int THREAD_NUM       = envInt("ARRAYMORPH_THREAD_NUM",         256);

extern std::string BUCKET_NAME;

typedef struct Result {
  std::vector<char> data;
} Result;

enum QPlan { NONE = -1, GET = 0 };

enum SPlan { S3 = 0, GOOGLE, AZURE_BLOB };

extern SPlan SP;

#endif
