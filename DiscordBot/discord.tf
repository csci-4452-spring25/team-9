terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.93"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "Discord" {
  ami                    = data.aws_ami.ami.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.mcsubnet.id
  vpc_security_group_ids = [aws_security_group.discord.id]
  key_name               = "key-test"
  user_data = templatefile("user_data.sh.tpl", {
    discordbot   = file("${path.module}/discordbot.py"),
    env_file     = file("${path.module}/.env"),
    requirements = file("${path.module}/requirements.txt"),
    service      = file("${path.module}/discord.service")
  })
  tags = {
    Name = "Discord Bot"
  }
}

resource "aws_security_group" "discord" {
  name   = "Discord SG"
  vpc_id = aws_vpc.mcvpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Discord SG"
  }
}

data "aws_ami" "ami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.7.202*-kernel-6.1-x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

