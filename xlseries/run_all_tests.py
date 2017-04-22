import nose
import os


def main():
    # make sure you run the tests from the directory where this module is
    old_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    args = ["nosetests", "--with-doctest"]
    nose.run(argv=args)

    os.chdir(old_dir)

if __name__ == '__main__':
    main()
