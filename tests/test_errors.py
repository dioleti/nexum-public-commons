import inspect
import unittest

import nexum


class TestNexumErrors(unittest.TestCase):
  def test_base_error(self):
    err = nexum.NexumError("teste")
    self.assertEqual(str(err), "[Nexum] Error: teste")

  def test_all_generated_errors(self):
    for name in nexum.__all__:
      cls = getattr(nexum, name, None)

      # Ignorar qualquer coisa que não seja classe
      if not inspect.isclass(cls):
        continue

      # Ignorar classes que não são exceções
      if not issubclass(cls, Exception):
        continue

      # Ignorar a classe base
      if cls is nexum.NexumError:
        continue

      with self.assertRaises(cls) as ctx:
        raise cls("mensagem")

      msg = str(ctx.exception)
      self.assertIn("[Nexum]", msg)
      self.assertIn(name.replace("Nexum", ""), msg)
      self.assertIn("mensagem", msg)


if __name__ == "__main__":
  unittest.main()
