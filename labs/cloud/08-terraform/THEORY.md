# Terraform IaC - THEORY

## Overview

Terraform is an Infrastructure as Code (IaC) tool that allows you to define and provision cloud infrastructure using declarative configuration files.

## 1. Core Concepts

### What is IaC?
- Version-controlled infrastructure definitions
- Reproducible environments
- Automated provisioning
- Drift detection

### Terraform Workflow

```
┌────────────────┐
│    Write       │  Create .tf files
└───────┬────────┘
        │
        ▼
┌────────────────┐
│    Plan        │  Preview changes
└───────┬────────┘
        │
        ▼
┌────────────────┐
│    Apply       │  Provision infrastructure
└───────┬────────┘
        │
        ▼
┌────────────────┐
│   Manage       │  Update/destroy resources
└────────────────┘
```

## 2. Terraform Configuration

### Basic Structure

```hcl
# providers.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

### Resources

```hcl
# main.tf
resource "aws_instance" "app" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  
  tags = {
    Name        = "app-server"
    Environment = "production"
  }
}
```

### Variables

```hcl
# variables.tf
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "Must be dev, staging, or prod."
  }
}
```

### Outputs

```hcl
# outputs.tf
output "instance_ip" {
  description = "Public IP of the instance"
  value       = aws_instance.app.public_ip
}

output "instance_arn" {
  description = "ARN of the instance"
  value       = aws_instance.app.arn
}
```

## 3. State Management

### Local State
```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

### Remote State (S3)
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### State Locking
- Prevents concurrent modifications
- DynamoDB table for AWS
- Always use with remote state

## 4. Modules

### Module Structure
```
modules/
├── networking/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
├── compute/
│   └── ...
└── database/
    └── ...
```

### Using Modules

```hcl
module "vpc" {
  source  = "./modules/networking"
  
  environment = "production"
  cidr_block  = "10.0.0.0/16"
  
  tags = {
    Project     = "MyApp"
    ManagedBy   = "Terraform"
  }
}
```

### Module Sources
```hcl
# Local
source = "./modules/networking"

# Terraform Registry
source = "terraform-aws-modules/vpc/aws"
version = "3.0.0"

# Git
source = "git::(link removed)//modules/networking?ref=v1.0.0"
```

## 5. Workspaces

```bash
# Create workspace
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# List workspaces
terraform workspace list
```

### Workspace Configuration

```hcl
terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "${terraform.workspace}/terraform.tfstate"
  }
}
```

## 6. Provisioners

### Local Exec
```hcl
resource "aws_instance" "app" {
  # ... instance config ...
  
  provisioner "local-exec" {
    command = "echo ${self.public_ip} > inventory.txt"
  }
}
```

### Remote Exec
```hcl
resource "aws_instance" "app" {
  # ... instance config ...
  
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
  }
  
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx"
    ]
  }
}
```

## 7. Data Sources

```hcl
# Get latest AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  
  filter {
    name   = "name"
    values = ["ubuntu-minimal/images/*ubuntu-jammy-22.04-amd64*"]
  }
}

# Get subnet info
data "aws_subnet" "selected" {
  id = var.subnet_id
}
```

## 8. Functions

### Common Functions
```hcl
# String functions
lookup(var.tags, "Environment", "default")

# Numeric functions
max(1, 2, 3)
min(1, 2, 3)

# Collection functions
length(var.security_groups)
contains(var.allowed_ips, "10.0.0.0/16")

# File functions
file("templates/init.sh")
templatefile("templates/init.tf", {
  hostname = "app.example.com"
})
```

## 9. Best Practices

### State Management
1. Use remote backend (S3)
2. Enable state encryption
3. Use DynamoDB for locking
4. Never commit state to git

### Module Design
1. Version pinned modules
2. Document inputs/outputs
3. Use for loops for multiple resources
4. Validate inputs

### Security
1. Use variables for secrets
2. Use SSM Parameter Store for sensitive data
3. Enable encryption at rest
4. Use IAM roles, not access keys

### Code Organization
```
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── locals.tf
├── terraform.tfvars
└── versions.tf
```

## Summary

Terraform provides:
1. **Declarative** infrastructure definition
2. **State** management and tracking
3. **Plan** before apply workflow
4. **Modules** for reusability
5. **Workspaces** for environments
6. **Provider** ecosystem (AWS, Azure, GCP, etc.)