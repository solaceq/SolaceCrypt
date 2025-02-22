class JuliaHandler:
    def __init__(self):
        try:
            import julia
            self.julia = julia.Julia()
            self.crypto = self.julia.include("src/crypto/advanced_crypto.jl")
            self.available = True
        except ImportError:
            self.available = False 