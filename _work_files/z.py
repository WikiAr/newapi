import os
from pathlib import Path


def generate_domain_test_placeholders(src_root, test_root):
    """
    ينشئ ملفات اختبار تجريبية مع نص وصفي داخلها للمسارات المحددة فقط.
    """
    src_path = Path(src_root)
    test_base = Path(test_root)

    for root, dirs, files in os.walk(src_path):
        current_path = Path(root)

        # التركيز فقط على مجلدات domain
        if "domain" not in current_path.parts:
            continue

        # استخراج المسار النسبي من بعد مجلد المشروع (مثلاً: admin/domain/db)
        # نستخدم current_path.relative_to(src_path) للحصول على المسار داخل src/x
        rel_path = current_path.relative_to(src_path)
        target_dir = test_base / rel_path

        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_stem = Path(file).stem

                # تحديد اسم ملف الاختبار
                if "models" in current_path.parts:
                    test_filename = f"test_{file_stem}_model.py"
                else:
                    test_filename = f"test_{file_stem}.py"

                # إنشاء المجلد إذا لم يكن موجوداً
                target_dir.mkdir(parents=True, exist_ok=True)
                test_file_path = target_dir / test_filename

                # المسار الذي سيظهر في النص الوصفي (مثلاً domain/models/user.py)
                # نبحث عن موقع word "domain" وما بعدها
                parts = current_path.parts
                domain_index = parts.index("domain")
                internal_path = "/".join(parts[domain_index:])

                content = f'"""\nUnit tests for {internal_path}/{file} module.\n"""\n'
                content_new = f'"""\nUnit tests for {internal_path}/{file} module.\nTODO: write tests\n"""\n'

                if test_file_path.exists():
                    text = test_file_path.read_text(encoding="utf-8")
                    if content.strip() == text.strip():
                        with open(test_file_path, "w", encoding="utf-8") as f:
                            f.write(content_new)


if __name__ == "__main__":
    main_dir = Path(__file__).parent.parent
    SOURCE_DIR = main_dir / "newapi"
    TEST_DIR = main_dir / "tests/unit"

    generate_domain_test_placeholders(SOURCE_DIR, TEST_DIR)
