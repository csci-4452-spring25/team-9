resource "aws_vpc" "mcvpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "Minecraft VPC"
  }
}

resource "aws_subnet" "mcsubnet" {
  vpc_id                  = aws_vpc.mcvpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "Minecraft subnet"
  }
}

resource "aws_internet_gateway" "gateway" {
  vpc_id = aws_vpc.mcvpc.id
  tags = {
    Name = "Minecraft Gateway"
  }
}

resource "aws_route_table" "route_table" {
  vpc_id = aws_vpc.mcvpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gateway.id
  }
  tags = {
    Name = "Public Routing"
  }
}

resource "aws_route_table_association" "route_table_association" {
  subnet_id      = aws_subnet.mcsubnet.id
  route_table_id = aws_route_table.route_table.id
}
