use std::fs;

fn main() {
    let content = fs::read_to_string("src/nexum/errors.py").unwrap();

    let mut errors = Vec::new();
    let mut inside_list = false;

    let mut all_items: Vec<String> = Vec::new();
    let mut inside_all = false;

    for line in content.lines() {
        let trimmed = line.trim();

        if trimmed.starts_with("BASE_ERRORS") && trimmed.contains("[") {
            inside_list = true;

            let start = trimmed.find('[').unwrap() + 1;
            let rest = &trimmed[start..];

            if rest.contains("]") {
                let end = rest.find(']').unwrap();
                let items = &rest[..end];

                for item in items.split(',') {
                    let name = item.trim();
                    if !name.is_empty() {
                        errors.push(name.to_string());
                    }
                }

                inside_list = false;
            }
        } else if inside_list {
            if trimmed.contains("]") {
                inside_list = false;
            } else {
                let item = trimmed.trim_end_matches(',');
                if !item.is_empty() {
                    errors.push(item.to_string());
                }
            }
        }

        if trimmed.starts_with("__all__") && trimmed.contains("[") {
            inside_all = true;

            let start = trimmed.find('[').unwrap() + 1;
            let rest = &trimmed[start..];

            if rest.contains("]") {
                let end = rest.find(']').unwrap();
                let items = &rest[..end];

                for item in items.split(',') {
                    let item = item.trim();
                    if item.starts_with('"') && item.ends_with('"') {
                        all_items.push(item.trim_matches('"').to_string());
                    }
                }

                inside_all = false;
            }
        } else if inside_all {
            if trimmed.contains("]") {
                inside_all = false;
            } else {
                let item = trimmed.trim_end_matches(',');
                if item.starts_with('"') && item.ends_with('"') {
                    all_items.push(item.trim_matches('"').to_string());
                }
            }
        }
    }

    let mut pyi = String::new();

    pyi.push_str("BASE_ERRORS: list[str]\n\n");
    pyi.push_str("class NexumError(Exception): ...\n");

    for err in &errors {
        pyi.push_str(&format!("class Nexum{err}(NexumError, {err}): ...\n"));
    }

    pyi.push_str("\n__all__: list[str] = [\n");

    for item in &all_items {
        pyi.push_str(&format!("    \"{item}\",\n"));
    }

    pyi.push_str("    \"NexumError\",\n");
    for err in &errors {
        pyi.push_str(&format!("    \"Nexum{err}\",\n"));
    }

    pyi.push_str("]\n");

    fs::write("src/nexum/errors.pyi", pyi).unwrap();

    println!("Arquivo errors.pyi gerado com sucesso!");
}
