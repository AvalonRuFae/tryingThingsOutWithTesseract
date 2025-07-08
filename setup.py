from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="student-composition-corrector",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An automated system for correcting student compositions using OCR and AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/student-composition-corrector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "composition-corrector=src.core.test_ocr_coordinates:main",
        ],
    },
)
