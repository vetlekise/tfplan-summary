terraform {
  required_providers {
    mock = {
      source = "liamcervante/mock"
      version = "0.2.0"
    }
  }
}

provider "mock" {
  # Configuration options
}

resource "mock_simple_resource" "1" {
  integer = 2
}

resource "mock_simple_resource" "2" {
  integer = 2
}

resource "mock_simple_resource" "3" {
  integer = 3
}

resource "mock_simple_resource" "4" {
  integer = 4
}
/*
data "mock_simple_resource" "4" {
  id = "4"
}
*/
