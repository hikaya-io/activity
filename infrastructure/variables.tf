variable "cluster_name"{
  description="cluster name"
}

variable "cluster_region" {
  description="region of the kubernetes cluster"
}

variable "kubernetes_version" {
  description="version of kubernetes to be used"
}

variable "node_type" {
  description="type of nodes used as worker nodes"
}
variable "max_node_number" {
  description="number of maximum nodes"
}

variable "min_node_number" {
  description="number of maximum nodes"
}
variable "digital_ocean_token" {
  description="digital ocean access token"
}

variable "db_size" {
  description="db node type and size"
}

variable "postgres_version" {
  description="version of postgres used"
}

variable "db_name" {
  description="name of the db to be created"
}

variable "tags" {
  description="project name"
}
