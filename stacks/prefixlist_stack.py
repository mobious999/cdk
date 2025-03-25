from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class PrefixListStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = config.get("env_name", "dr")
        tags = config.get("tags", {})
        prefix_lists_cfg = config.get("prefix_lists", {})

        self.prefix_lists = {}

        for name, entries in prefix_lists_cfg.items():
            # Generate prefix list entries
            prefix_entries = []
            for entry in entries:
                prefix_entries.append({
                    "cidr": entry["cidr"],
                    "description": entry.get("description", "Managed by CDK")
                })

            # Create the prefix list
            prefix_list = ec2.CfnPrefixList(
                self, f"{name}PrefixList",
                address_family="IPv4",
                max_entries=len(prefix_entries),
                prefix_list_name=f"{env_name}-{name}",
                entries=prefix_entries
            )

            Tags.of(prefix_list).add("Name", f"{env_name}-{name}")
            for k, v in tags.items():
                Tags.of(prefix_list).add(k, v)

            # Store prefix list ID reference
            self.prefix_lists[name] = prefix_list.ref  # or use .attr_prefix_list_id for full ARN
