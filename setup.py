from setuptools import setup
setup(
    name="ECRScan",
    version='0.2.0',
    packages=['ecrscan'],
    description='ECR scan utility',
    author='Chuck Muckamuck',
    author_email='Chuck.Muckamuck@gmail.com',
    install_requires=[
        "boto3>=1.10",
        "Click>=6.7",
        "tabulate>=0.8",
        "configparser"
    ],
    entry_points="""
        [console_scripts]
        ecrscan=ecrscan.command:cli
    """
)
