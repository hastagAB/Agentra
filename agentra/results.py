"""
Save and load evaluation results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from .types import EvaluationResult, Status, CategoryResult, TraceResult


def save_result(
    result: EvaluationResult,
    name: str,
    results_dir: str = "agentra-results",
) -> str:
    """
    Save evaluation result to JSON file.
    
    Args:
        result: The evaluation result
        name: Name for this result (e.g., "auth-flow-test", "v2.1-regression")
        results_dir: Directory to save results
    
    Returns:
        Path to saved file
    """
    
    # Create directory if needed
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    
    # Set name on result
    result.name = name
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)
    
    # Convert to dict and save
    data = _result_to_dict(result)
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath


def load_result(name: str, results_dir: str = "agentra-results") -> EvaluationResult:
    """
    Load evaluation result from file.
    
    Args:
        name: Exact filename or name prefix (loads most recent if prefix)
        results_dir: Directory containing results
    
    Returns:
        EvaluationResult
    """
    
    results_path = Path(results_dir)
    
    if not results_path.exists():
        raise FileNotFoundError(f"Results directory not found: {results_dir}")
    
    # Try exact match first
    exact_path = results_path / f"{name}.json"
    if exact_path.exists():
        return _load_from_path(exact_path)
    
    # If name already ends with .json, try that
    if name.endswith(".json"):
        exact_path = results_path / name
        if exact_path.exists():
            return _load_from_path(exact_path)
    
    # Find most recent matching prefix
    matches = list(results_path.glob(f"{name}*.json"))
    if not matches:
        raise FileNotFoundError(f"No results found matching '{name}'")
    
    # Sort by modification time, get most recent
    most_recent = max(matches, key=lambda p: p.stat().st_mtime)
    return _load_from_path(most_recent)


def list_results(results_dir: str = "agentra-results") -> list[dict]:
    """
    List all saved results.
    
    Returns:
        List of {name, filename, timestamp, score, status}
    """
    
    results_path = Path(results_dir)
    if not results_path.exists():
        return []
    
    results = []
    for filepath in results_path.glob("*.json"):
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            results.append({
                "name": data.get("name", filepath.stem),
                "filename": filepath.name,
                "timestamp": data.get("timestamp"),
                "score": data.get("score"),
                "status": data.get("status"),
                "traces": data.get("total_traces"),
            })
        except:
            pass
    
    # Sort by timestamp descending
    results.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return results


def compare_results(
    names: list[str],
    results_dir: str = "agentra-results",
) -> str:
    """
    Compare multiple results and return comparison report.
    """
    
    results = [load_result(name, results_dir) for name in names]
    
    lines = ["COMPARISON REPORT", "=" * 60, ""]
    
    # Header
    header = f"{'Metric':<20}"
    for r in results:
        header += f"{r.name:<15}"
    lines.append(header)
    lines.append("-" * 60)
    
    # Overall score
    row = f"{'Overall Score':<20}"
    for r in results:
        row += f"{r.score:.0%:<15}"
    lines.append(row)
    
    # Status
    row = f"{'Status':<20}"
    for r in results:
        row += f"{r.status.value:<15}"
    lines.append(row)
    
    # Category scores
    lines.append("")
    lines.append("Category Scores:")
    
    # Get all category names
    cat_names = list(set(c.name for r in results for c in r.categories))
    
    for cat_name in cat_names:
        row = f"  {cat_name:<18}"
        for r in results:
            cat = next((c for c in r.categories if c.name == cat_name), None)
            score = f"{cat.score:.0%}" if cat else "N/A"
            row += f"{score:<15}"
        lines.append(row)
    
    return "\n".join(lines)


def _result_to_dict(result: EvaluationResult) -> dict:
    """Convert EvaluationResult to JSON-serializable dict."""
    data = asdict(result)
    
    # Convert Status enum to string
    data["status"] = result.status.value
    
    # Convert datetime objects
    if isinstance(result.timestamp, datetime):
        data["timestamp"] = result.timestamp.isoformat()
    
    return data


def _load_from_path(path: Path) -> EvaluationResult:
    """Load EvaluationResult from JSON file."""
    with open(path) as f:
        data = json.load(f)
    
    # Convert status string back to enum
    if "status" in data:
        data["status"] = Status(data["status"])
    
    # Convert timestamp string back to datetime
    if "timestamp" in data and isinstance(data["timestamp"], str):
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
    
    # Reconstruct nested objects
    if "categories" in data:
        data["categories"] = [
            CategoryResult(**cat) for cat in data["categories"]
        ]
    
    if "trace_results" in data:
        data["trace_results"] = [
            TraceResult(
                **{k: v for k, v in tr.items() if k != "categories"},
                categories=[CategoryResult(**cat) for cat in tr.get("categories", [])]
            )
            for tr in data["trace_results"]
        ]
    
    return EvaluationResult(**data)

