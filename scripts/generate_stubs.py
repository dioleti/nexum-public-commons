import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class GenerateStubsHook(BuildHookInterface):
  def initialize(self, version, build_data):
    subprocess.run(
      ["cargo", "run", "--manifest-path", "scripts/Cargo.toml"],
      check=True
    )
