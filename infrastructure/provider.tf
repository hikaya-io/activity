# Set provsider to digital ocean platform to indicate to terraform
# that resources to be created will be on terraform
# Authenticate the creation of the cluster with digital ocean access
# token
provider "digitalocean" {
  version = ">= 1.8.0"
  token   = var.digital_ocean_token
}
