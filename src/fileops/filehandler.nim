import os, streams

type
  FileHandler* = object
    chunkSize: int

proc newFileHandler*(): FileHandler =
  FileHandler(chunkSize: 64 * 1024)  # 64KB chunks

proc fastCopy*(self: FileHandler, source, dest: string) =
  var
    srcFile = newFileStream(source, fmRead)
    dstFile = newFileStream(dest, fmWrite)
    buffer = newString(self.chunkSize)
  
  while not srcFile.atEnd:
    let bytesRead = srcFile.readData(addr buffer[0], self.chunkSize)
    if bytesRead > 0:
      dstFile.writeData(addr buffer[0], bytesRead)

  srcFile.close()
  dstFile.close() 