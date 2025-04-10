variable "region_id" {
  type        = string
  default     = "us-east-1"
  description = "Region where you want the server"
}

variable "instance_type" {
  type        = string
  default     = "t2.small"
  description = "instance type"
}

variable "mojang_server_url" {
  type        = string
  default     = "https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar"
  description = "mojang server download; default is the latest server 1.21.5"
}
