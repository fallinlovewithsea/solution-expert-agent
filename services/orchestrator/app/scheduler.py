from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


def start_scheduler():
    # 每天凌晨 2 点采集行业数据
    scheduler.add_job(
        _trigger_collection,
        "cron",
        hour=2,
        minute=0,
        id="daily_xhs_collection",
    )
    # 每天凌晨 4 点执行知识蒸馏
    scheduler.add_job(
        _trigger_distill,
        "cron",
        hour=4,
        minute=0,
        id="daily_knowledge_distill",
    )
    scheduler.start()
    print("[Scheduler] 定时任务已启动")


def _trigger_collection():
    """触发数据采集任务"""
    from app.worker import collect_xhs_data
    collect_xhs_data.delay("母婴", ["伊利", "君乐宝"], "飞鹤")
    print("[Scheduler] 已触发小红书数据采集任务")


def _trigger_distill():
    """触发知识蒸馏任务"""
    from app.worker import distill_knowledge, distill_xhs_data
    distill_knowledge.delay()
    distill_xhs_data.delay()
    print("[Scheduler] 已触发知识蒸馏任务")