module PureOps where

import qualified Data.ByteString as BS
import qualified Data.ByteString.Char8 as C8
import qualified Crypto.Hash.SHA256 as SHA256
import Data.Binary (encode, decode)

-- Pure password strength checker
data PasswordStrength = Weak | Medium | Strong deriving (Show, Eq)

checkPasswordStrength :: String -> PasswordStrength
checkPasswordStrength pass = case (length pass, hasUpper, hasLower, hasNum, hasSpecial) of
    (l, True, True, True, True) | l >= 12 -> Strong
    (l, _, _, _, _) | l >= 8 -> Medium
    _ -> Weak
  where
    hasUpper = any isUpper pass
    hasLower = any isLower pass
    hasNum = any isNumber pass
    hasSpecial = any (`elem` "!@#$%^&*()") pass

-- Pure file splitting for parallel processing
splitFileContent :: BS.ByteString -> Int -> [BS.ByteString]
splitFileContent content chunkSize = 
    if BS.null content
    then []
    else let (chunk, rest) = BS.splitAt chunkSize content
         in chunk : splitFileContent rest chunkSize 