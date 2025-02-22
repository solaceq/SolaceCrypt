require "http/client"
require "json"

class RemoteBackup
  class Config
    JSON.mapping(
      endpoint: String,
      api_key: String,
      timeout: Int32
    )
  end

  def initialize(@config : Config)
    @client = HTTP::Client.new(URI.parse(@config.endpoint))
    @client.connect_timeout = @config.timeout
  end

  def backup(file_path : String) : Bool
    File.open(file_path) do |file|
      response = @client.post(
        "/backup",
        headers: HTTP::Headers{
          "Authorization" => "Bearer #{@config.api_key}",
          "Content-Type" => "application/octet-stream"
        },
        body: file
      )
      return response.success?
    end
  end
end 