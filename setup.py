from setuptools import setup, find_packages

setup(
    name="military-training-plan",
    version="1.0.0",
    description="Ứng dụng Quản lý Kế hoạch Huấn luyện",
    author="Victor Howard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6>=6.6.0",
        "openpyxl>=3.1.2",
        "reportlab>=4.0.7",
        "Pillow>=10.2.0",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "military-training-plan=main:main",
        ],
    },
)

