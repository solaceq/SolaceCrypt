const std = @import("std");
const mem = std.mem;
const Allocator = std.mem.Allocator;

pub const SecureMemory = struct {
    data: []u8,
    allocator: *Allocator,

    pub fn init(allocator: *Allocator, size: usize) !SecureMemory {
        const data = try allocator.alloc(u8, size);
        return SecureMemory{
            .data = data,
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *SecureMemory) void {
        // Securely wipe memory before deallocation
        mem.secureZero(u8, self.data);
        self.allocator.free(self.data);
    }

    pub fn write(self: *SecureMemory, data: []const u8) !void {
        if (data.len > self.data.len) return error.BufferTooSmall;
        mem.copy(u8, self.data, data);
    }
}; 