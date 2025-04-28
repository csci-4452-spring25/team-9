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

resource "aws_iam_role_policy" "iam_policy" {
  name = "iam_policy"
  role = aws_iam_role.iam_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:*",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "iam_role" {
  name = "discord_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attachment" {
  role       = aws_iam_role.iam_role.name
  policy_arn = aws_iam_policy.iam_policy.arn
}

resource "aws_iam_instance_profile" "iam_profile" {
  name = "Discord-Profile"
  role = aws_iam_role.iam_role.name
}
