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
  region = var.region_id
}

resource "aws_instance" "minecraft" {
  ami                    = data.aws_ami.ami.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.minecraft.id]
  subnet_id              = aws_subnet.mcsubnet.id
  key_name               = "key-test"
  user_data              = <<-EOF
    #!/bin/bash
    MINECRAFTSERVERURL=${var.mojang_server_url}
    sudo yum install -y java-21-amazon-corretto-headless
    adduser minecraft
    mkdir /opt/minecraft/
    mkdir /opt/minecraft/server/
    cd /opt/minecraft/server
    wget $MINECRAFTSERVERURL
    java -Xmx1300M -Xms1300M -jar server.jar nogui
    sleep 40
    sed -i 's/false/true/p' eula.txt
    touch start
    printf '#!/bin/bash\ncd /opt/minecraft/server\nsudo java -Xmx1300M -Xms1300M -jar server.jar nogui\n' >> start
    chmod +x start
    sleep 1
    touch stop
    printf '#!/bin/bash\ncd /opt/minecraft/server\nsudo kill -9 $(ps -ef | pgrep -f "java")' >> stop
    chmod +x stop
    sleep 1
    cd /etc/systemd/system
    touch minecraft.service
    printf '[Unit]\nDescription=Minecraft Server on start up\nWants=network-online.target\n[Service]\nUser=minecraft\nWorkingDirectory=/opt/minecraft/server\nExecStart=/opt/minecraft/server/start\nStandardInput=null\n[Install]\nWantedBy=multi-user.target' >> minecraft.service
    sudo systemctl daemon-reload
    sudo systemctl start minecraft.service
    sudo systemctl enable minecraft.service
    EOF
  tags = {
    Name = "Minecraft Server"
  }
}

resource "aws_security_group" "minecraft" {
  name   = "Minecraft SG"
  vpc_id = aws_vpc.mcvpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 25565
    to_port     = 25565
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
    Name = "Minecraft Server"
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

