#!/bin/bash

# Build Nim components
nim c -d:release src/fileops/filehandler.nim

# Build Zig components
zig build-lib src/system/secure_mem.zig

# Build Crystal components
crystal build src/network/remote_backup.cr

# Build Julia components
julia --compile=all -e 'include("src/crypto/advanced_crypto.jl")'

# Build Kotlin UI
kotlinc src/ui/KotlinUI.kt -include-runtime -d solacecrypt-ui.jar

# Build Haskell components
ghc -O2 src/functional/pure_ops.hs 