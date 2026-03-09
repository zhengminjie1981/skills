#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for knowledge index manager"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with underscore filename
import importlib.util
spec = importlib.util.spec_from_file_location("knowledge_index_manager",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "scripts", "knowledge-index-manager.py"))
kim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kim)
KnowledgeBaseManager = kim.KnowledgeBaseManager

def test_wikilink_parsing():
    """Test wikilink extraction"""
    m = KnowledgeBaseManager(enable_ai_summary=False)

    links = m.extract_wikilinks('See [[doc1]] and [[doc2#section|alias]] and [[folder/doc3]]')
    print('Wikilink parsing test:')
    print('  Input: See [[doc1]] and [[doc2#section|alias]] and [[folder/doc3]]')
    print('  Output:', links)
    assert links == ['doc1', 'doc2', 'folder/doc3'], f'Expected [doc1, doc2, folder/doc3], got {links}'
    print('  PASS')
    return True

def test_tag_extraction():
    """Test tag extraction from frontmatter and content"""
    m = KnowledgeBaseManager(enable_ai_summary=False)

    content = '''---
tags: [api, auth]
---
# API Auth
This is a #security document.
'''
    tags_fm = m.extract_frontmatter_tags(content)
    tags_content = m.extract_content_tags(content)

    print('\nTag extraction test:')
    print('  Frontmatter tags:', tags_fm)
    print('  Content tags:', tags_content)
    assert 'api' in tags_fm and 'auth' in tags_fm
    assert 'security' in tags_content
    print('  PASS')
    return True

def test_content_hash():
    """Test content hashing for caching"""
    m = KnowledgeBaseManager(enable_ai_summary=False)

    hash1 = m.get_content_hash('test content')
    hash2 = m.get_content_hash('test content')
    hash3 = m.get_content_hash('different content')

    print('\nContent hash test:')
    print('  Hash 1:', hash1)
    print('  Hash 2:', hash2)
    print('  Hash 3:', hash3)
    assert hash1 == hash2, 'Same content should produce same hash'
    assert hash1 != hash3, 'Different content should produce different hash'
    print('  PASS')
    return True

def test_query_keyword_extraction():
    """Test query keyword extraction"""
    m = KnowledgeBaseManager(enable_ai_summary=False)

    keywords = m._extract_query_keywords('GitLab CI/CD 配置，如何设置流水线？')
    print('\nQuery keyword extraction test:')
    print('  Input: GitLab CI/CD 配置，如何设置流水线？')
    print('  Output:', keywords)
    assert 'gitlab' in keywords
    assert 'ci/cd' in keywords or 'ci' in keywords
    print('  PASS')
    return True

def main():
    """Run all tests"""
    print('='*60)
    print('Running unit tests')
    print('='*60)

    tests = [
        test_wikilink_parsing,
        test_tag_extraction,
        test_content_hash,
        test_query_keyword_extraction,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f'  FAIL: {e}')
            failed += 1

    print('\n' + '='*60)
    print(f'Results: {passed} passed, {failed} failed')
    print('='*60)

    return failed == 0

if __name__ == '__main__':
    sys.exit(0 if main() else 1)
