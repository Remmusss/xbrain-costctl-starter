"""clean - (stretch) bulk terminate resources matching a tag.

WARNING - DESIGN-FOR-SAFETY
---------------------------
This is the most dangerous command in the CLI. Get the contract right:

  1. DEFAULT IS DRY-RUN. Without --apply the command MUST NOT touch resources.
     It only lists what WOULD be deleted.
  2. Even with --apply, you should consider printing a summary count first
     ("about to terminate N EC2 + M volumes - proceed?"), though for this
     starter a hard `--apply` flag is enough.
  3. Never use this with a tag you don't fully own. Reflection prompt in
     README covers the blast-radius scenario.
"""
import boto3

from commands._common import parse_kv


def _find_targets(tag_key, tag_val):
    """Return {"ec2": [...], "volume": [...]} matching tag in non-terminal state."""
    ec2 = boto3.client("ec2")
    targets = {"ec2": [], "volume": []}

    inst_pages = ec2.get_paginator("describe_instances").paginate(
        Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_val]}]
    )
    for page in inst_pages:
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                state = instance["State"]["Name"]
                if state not in ("shutting-down", "terminated"):
                    targets["ec2"].append(instance["InstanceId"])

    vol_pages = ec2.get_paginator("describe_volumes").paginate(
        Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_val]}]
    )
    for page in vol_pages:
        for volume in page.get("Volumes", []):
            if volume["State"] == "available":
                targets["volume"].append(volume["VolumeId"])

    return targets


def run(args):
    """Entry point.

    Args set by argparse:
        args.tag    — "key=value" string (REQUIRED)
        args.apply  — bool, must be True to actually delete (default False = dry-run)
    """
    tag_key, tag_val = parse_kv(args.tag)
    targets = _find_targets(tag_key, tag_val)
    ec2_ids = targets["ec2"]
    volume_ids = targets["volume"]

    if not ec2_ids and not volume_ids:
        print(f"Nothing to clean for {tag_key}={tag_val}.")
        return

    print(
        f"Found {len(ec2_ids)} EC2 and {len(volume_ids)} volume(s) "
        f"for {tag_key}={tag_val}."
    )

    if not args.apply:
        print("dry-run - pass --apply to terminate/delete these resources.")
        return

    ec2 = boto3.client("ec2")
    if ec2_ids:
        ec2.terminate_instances(InstanceIds=ec2_ids)
        print(f"Terminated {len(ec2_ids)} EC2 instance(s).")

    for volume_id in volume_ids:
        ec2.delete_volume(VolumeId=volume_id)
        print(f"Deleted volume {volume_id}.")


