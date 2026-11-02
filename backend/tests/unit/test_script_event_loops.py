"""Tests proving database scripts execute work and cleanup in ONE event loop (calling asyncio.run exactly once)."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from scripts import (
    create_indexes,
    import_schemes,
    review_schemes,
    seed_admin,
    seed_schemes,
)

DATABASE_SCRIPTS = [
    create_indexes,
    import_schemes,
    review_schemes,
    seed_admin,
    seed_schemes,
]


def test_scripts_call_asyncio_run_exactly_once() -> None:
    """Verify that calling main() in every database script calls asyncio.run at most once."""
    for script_mod in DATABASE_SCRIPTS:
        def fake_run(coro):
            if hasattr(coro, "close"):
                coro.close()
            return 0

        with patch("asyncio.run", side_effect=fake_run) as mock_run:
            # Provide required arguments so scripts parse args cleanly
            args = [script_mod.__file__]
            if script_mod is seed_schemes:
                args.append("--confirm")

            with patch("sys.argv", args):
                try:
                    if hasattr(script_mod, "main"):
                        script_mod.main()
                except SystemExit:
                    pass

            assert mock_run.call_count == 1, (
                f"{script_mod.__name__}.main() called asyncio.run "
                f"{mock_run.call_count} times; expected exactly 1."
            )


def test_scripts_ast_no_multiple_asyncio_run() -> None:
    """AST static analysis: prove no database script calls asyncio.run multiple times in main()."""
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
    db_script_filenames = [
        "create_indexes.py",
        "import_schemes.py",
        "review_schemes.py",
        "seed_admin.py",
        "seed_schemes.py",
    ]

    for fname in db_script_filenames:
        file_path = scripts_dir / fname
        assert file_path.is_file(), f"Script not found: {file_path}"
        code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(code, filename=str(file_path))

        # Find main function definition
        main_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                main_def = node
                break

        assert main_def is not None, f"main() function not found in {fname}"

        # Count occurrences of asyncio.run calls inside main()
        asyncio_run_calls = []
        for node in ast.walk(main_def):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "run":
                    if isinstance(func.value, ast.Name) and func.value.id == "asyncio":
                        asyncio_run_calls.append(node)

        assert len(asyncio_run_calls) <= 1, (
            f"{fname} has {len(asyncio_run_calls)} calls to asyncio.run() inside main(); "
            "must be called at most once."
        )


@pytest.mark.asyncio
async def test_import_schemes_async_main_cleans_up_client() -> None:
    """Verify _async_main in import_schemes executes close_client in finally block."""
    with patch("scripts.import_schemes.MongoDBManager.close_client") as mock_close:
        with patch("scripts.import_schemes.run_import", side_effect=RuntimeError("Simulated write error")):
            mock_args = MagicMock()
            mock_args.file = "dummy.json"
            mock_args.apply = False
            mock_args.update = False

            with pytest.raises(RuntimeError, match="Simulated write error"):
                await import_schemes._async_main(mock_args)

            mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_review_schemes_async_main_cleans_up_client() -> None:
    """Verify _async_main in review_schemes executes close_client in finally block."""
    with patch("scripts.review_schemes.MongoDBManager.close_client") as mock_close:
        with patch("scripts.review_schemes.run_review", side_effect=RuntimeError("Simulated review error")):
            mock_args = MagicMock()
            mock_args.slug = None

            with pytest.raises(RuntimeError, match="Simulated review error"):
                await review_schemes._async_main(mock_args)

            mock_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_seed_admin_async_main_cleans_up_client() -> None:
    """Verify _async_main in seed_admin executes close_client in finally block."""
    with patch("scripts.seed_admin.MongoDBManager.close_client") as mock_close:
        with patch("scripts.seed_admin.seed_first_admin", side_effect=RuntimeError("Simulated seed error")):
            with pytest.raises(RuntimeError, match="Simulated seed error"):
                await seed_admin._async_main()

            mock_close.assert_awaited_once()
