from python_template.__main__ import main


def test_main(capsys):
    # Capture the output of the main function
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\n"
