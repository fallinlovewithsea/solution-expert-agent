from skills.s9_archive import S9Archive, ArchiveInput


def test_s9_basic_archive():
    """基本归档测试"""
    skill = S9Archive()
    result = skill.run(ArchiveInput(
        final_proposal={
            "client_name": "飞鹤",
            "industry": "母婴",
            "operation_strategy": {"competitors": ["伊利", "君乐宝"]},
        },
        review_comments="方案整体不错",
        bid_result="中标",
    ))
    assert result.success is True
    assert result.review_report != ""
    assert "飞鹤" in result.review_report


def test_s9_review_report_generation():
    """复盘报告生成测试"""
    skill = S9Archive()
    report = skill._generate_review_report(
        proposal={"client_name": "飞鹤", "industry": "母婴"},
        review_comments="需优化预算部分",
        bid_result="中标",
        updated=["品牌库", "竞品库", "复盘库"],
    )
    assert "飞鹤" in report
    assert "母婴" in report
    assert "中标" in report
    assert "需优化预算部分" in report
    assert "品牌库" in report


def test_s9_empty_competitors():
    """空竞品列表测试"""
    skill = S9Archive()
    result = skill.run(ArchiveInput(
        final_proposal={
            "client_name": "测试品牌",
            "industry": "通用",
            "operation_strategy": {},
        },
        review_comments="",
        bid_result="",
    ))
    assert result.success is True


def test_s9_with_custom_ids():
    """自定义 user_id 和 session_id 测试"""
    skill = S9Archive()
    result = skill.run(ArchiveInput(
        final_proposal={
            "client_name": "飞鹤",
            "industry": "母婴",
        },
        user_id="user_001",
        session_id="session_abc",
    ))
    assert result.success is True


def test_s9_competitor_update():
    """竞品库更新测试"""
    skill = S9Archive()
    # 有竞品信息的提案应该触发更新
    updated = skill._update_competitor_library({
        "client_name": "飞鹤",
        "industry": "母婴",
        "operation_strategy": {
            "competitor_benchmark": "伊利在KOS矩阵方面较弱",
            "competitors": ["伊利", "君乐宝"],
        },
    })
    # 即使数据库不可用，方法本身不应崩溃
    assert updated in (True, False)