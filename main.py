from __future__ import annotations

from src.pipeline import run_pipeline


def main() -> None:
    summary = run_pipeline()
    print("Perfil cadastral com CadÚnico amostral")
    print("-" * 44)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
