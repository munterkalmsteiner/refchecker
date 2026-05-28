"""
Tests for GROBID reference extraction.

Tests the first 5 references from master thesis PDFs to verify:
1. Authors are extracted correctly (no editors mixed in)
2. Venue information is extracted for all reference types
3. DOI/arXiv identifiers are handled correctly
4. Titles are extracted correctly
"""

import os
import pytest
from src.refchecker.utils.grobid import extract_refs_via_grobid


# Test data structure: PDF filename -> list of expected first 5 references
EXPECTED_REFERENCES = {
    "indika.pdf": [
        # Reference 1
        {
            "authors": ['V Andrikopoulos', 'S Strauch', 'F Leymann'],
            "title": "Decision models for cloud migration and application containerization",
            "venue": "Software: Practice and Experience",
            "year": 2019,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
        # Reference 2
        {
            "authors": ['B Burns', 'B Grant', 'D Oppenheimer', 'E Brewer', 'J Wilkes'],
            "title": "Borg, omega, and kubernetes",
            "venue": "Communications of the ACM",
            "year": 2016,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
        # Reference 3
        {
            "authors": ['I Eranga'],
            "title": "Supplementary materials",
            "venue": "",
            "year": 2025,
            "doi": None,
            "url": "https://github.com/indikaeranga/Orchestration-Tool-Thesis-Supplementary-Materials",
            "notes": "Online resource",
        },
        # Reference 4
        {
            "authors": ['D Merkel'],
            "title": "Docker: Lightweight linux containers for consistent development and deployment",
            "venue": "Linux Journal",
            "year": 2014,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
        # Reference 5
        {
            "authors": ['C Pahl', 'A Brogi', 'J Soldani', 'P Jamshidi'],
            "title": "Cloud container technologies: A state-of-the-art review",
            "venue": "IEEE Transactions on Cloud Computing",
            "year": 2017,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
    ],
    "pan.pdf": [
        # Reference 1
        {
            "authors": ['A Bilal', 'D Ebert', 'B Lin'],
            "title": "Llms for explainable ai: A comprehensive survey",
            "venue": "",
            "year": 2025,
            "doi": None,
            "url": "https://arxiv.org/abs/arXiv:2504.00125",
            "notes": "arXiv preprint",
        },
        # Reference 2
        {
            "authors": ['E Cambria', 'L Malandri', 'F Mercorio', 'M Mezzanzanica', 'N Nobani'],
            "title": "A survey on xai and natural language explanations",
            "venue": "Information Processing & Management",
            "year": 2023,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
        # Reference 3
        {
            "authors": ['J Deyoung', 'S Jain', 'N F Rajani', 'E Lehman', 'C Xiong', 'R Socher', 'B C Wallace'],
            "title": "Eraser: A benchmark to evaluate rationalized nlp models",
            "venue": "Proceedings of the 58th annual meeting of the association for computational linguistics",
            "year": 2020,
            "doi": None,
            "url": "",
            "notes": "Conference paper",
        },
        # Reference 4
        {
            "authors": ['R Dwivedi', 'D Dave', 'H Naik', 'S Singhal', 'R Omer', 'P Patel', 'B Qian', 'Z Wen', 'T Shah', 'G Morgan'],
            "title": "Explainable ai (xai): Core ideas, techniques, and solutions",
            "venue": "ACM computing surveys",
            "year": 2023,
            "doi": None,
            "url": "",
            "notes": "Journal article",
        },
        # Reference 5
        {
            "authors": ['K Erdil', 'E Finn', 'K Keating', 'J Meattle', 'S Park', 'D Yoon'],
            "title": "Software maintenance as part of the software life cycle",
            "venue": "Software Engineering Project",
            "year": 2003,
            "doi": None,
            "url": "",
            "notes": "Report/project",
        },
    ],
}


@pytest.fixture
def pdf_fixtures_dir():
    """Return path to GROBID test fixtures directory."""
    return os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "grobid_extraction"
    )


@pytest.mark.parametrize("pdf_filename", EXPECTED_REFERENCES.keys())
def test_grobid_extracts_first_five_references(pdf_fixtures_dir, pdf_filename):
    """Test that GROBID extracts the first 5 references correctly from each PDF."""
    pdf_path = os.path.join(pdf_fixtures_dir, pdf_filename)
    
    # Skip if PDF not yet added
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF {pdf_filename} not yet added to fixtures")
    
    # Extract references via GROBID
    extracted_refs = extract_refs_via_grobid(pdf_path)
    
    # Get expected references for this PDF
    expected_refs = EXPECTED_REFERENCES[pdf_filename]
    
    # Check we have at least 5 references
    assert len(extracted_refs) >= 5, f"Expected at least 5 references, got {len(extracted_refs)}"
    
    # Test each of the first 5 references
    for i, expected in enumerate(expected_refs):
        actual = extracted_refs[i]
        
        # Skip empty expected data (not yet filled in)
        if not expected["title"] and not expected["authors"]:
            continue
        
        # Test authors (Issue #1: editors should not be included)
        assert actual["authors"] == expected["authors"], \
            f"Reference {i+1}: Authors mismatch. Note: {expected.get('notes', '')}"
        
        # Test title
        assert actual["title"] == expected["title"], \
            f"Reference {i+1}: Title mismatch"
        
        # Test venue (Issue #2: venue should be extracted even for book references)
        assert actual["venue"] == expected["venue"], \
            f"Reference {i+1}: Venue mismatch. Note: {expected.get('notes', '')}"
        
        # Test year
        assert actual["year"] == expected["year"], \
            f"Reference {i+1}: Year mismatch"
        
        # Test DOI
        assert actual["doi"] == expected["doi"], \
            f"Reference {i+1}: DOI mismatch"
        
        # Test URL (Issue #3: DOI/arXiv handling)
        assert actual["url"] == expected["url"], \
            f"Reference {i+1}: URL mismatch. Note: {expected.get('notes', '')}"


def test_authors_do_not_include_editors(pdf_fixtures_dir):
    """
    Specific test for Issue #1: Editors should not be extracted as authors.
    
    Reference 58 in 3712003.pdf is a proceedings volume with 3 editors
    (Lun-Wei Ku, Andre Martins, Vivek Srikumar) but NO authors.
    These editors should NOT appear in the authors list.
    """
    pdf_path = os.path.join(pdf_fixtures_dir, "3712003.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("3712003.pdf not yet added")
    
    extracted_refs = extract_refs_via_grobid(pdf_path)
    
    # Reference 58 (0-indexed as 57)
    assert len(extracted_refs) > 57, "Not enough references extracted"
    
    ref58 = extracted_refs[57]
    
    # The critical assertion: authors should be empty (editors should NOT be in authors)
    assert ref58["authors"] == [], \
        f"Expected no authors (only editors), but got: {ref58['authors']}"
    
    # Also verify other fields
    assert ref58["title"] == "Association for Computational Linguistics", \
        f"Title mismatch: {ref58['title']}"
    assert ref58["url"] == "https://aclanthology.org/2024.acl-long.269", \
        f"URL mismatch: {ref58['url']}"


def test_venue_extraction_for_book_references(pdf_fixtures_dir):
    """
    Specific test for Issue #2: Venue should be extracted for references
    that only have monogr (books, reports, etc.), not just journal articles.
    """
    pytest.skip("TODO: Need a book/report reference to test this issue")


def test_doi_and_arxiv_handling(pdf_fixtures_dir):
    """
    Specific test for Issue #3: DOI and arXiv identifiers should be
    handled correctly (first one wins, URL constructed properly).
    """
    # Test arXiv URL construction
    pdf_path = os.path.join(pdf_fixtures_dir, "pan.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("pan.pdf not yet added")
    
    extracted_refs = extract_refs_via_grobid(pdf_path)
    
    # Reference 1 from pan.pdf is an arXiv paper
    assert len(extracted_refs) >= 1, "Not enough references extracted"
    assert extracted_refs[0]["url"] == "https://arxiv.org/abs/arXiv:2504.00125", \
        "arXiv URL not constructed correctly"
    assert extracted_refs[0]["type"] == "arxiv", \
        "arXiv reference not marked with correct type"
