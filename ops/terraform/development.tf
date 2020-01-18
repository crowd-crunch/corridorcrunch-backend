provider "hcloud" {
  token = "${var.hcloud_token}"
}

resource "hcloud_server" "pz-dev-node-1" {
  name        = "pz-dev-node-1"
  server_type = "cx11"
  image       = "ubuntu-18.04"
  location    = "hel1"
  ssh_keys    = ["${hcloud_ssh_key.pz-dev-node-1-provisioning-key-1.id}"]
}

resource "hcloud_ssh_key" "pz-dev-node-1-provisioning-key-1" {
  name       = "pz-dev-node-1-provisioning-key-1"
  public_key = "${var.hcloud_provisioning_key}"
}

