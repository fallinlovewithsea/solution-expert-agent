from app.db.models import BrandInfo, CaseLabel, ProposalRecord


def test_brand_info_creation():
    brand = BrandInfo(
        brand_name="飞鹤",
        industry="母婴",
        sub_category="婴幼儿奶粉",
        current_status="已有基础KOS账号"
    )
    assert brand.brand_name == "飞鹤"
    assert brand.industry == "母婴"
    assert brand.contact_history == []


def test_case_label_creation():
    case = CaseLabel(
        case_name="林氏家居KOS代发代管案例",
        industry="家居家装",
        scene="KOS矩阵",
        playbook="代发代管",
        key_metrics={"账号数": 80, "月均笔记": 320}
    )
    assert case.case_name == "林氏家居KOS代发代管案例"
    assert case.key_metrics["账号数"] == 80