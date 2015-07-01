import nose

if __name__ == '__main__':
    args = ["nosetests", "--with-doctest", "--with-coverage",
            "--cover-package=xlseries"]
    nose.run(argv=args)
