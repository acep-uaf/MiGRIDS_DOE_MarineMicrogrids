# Widget, method, String, String, String,String -> QtQidget.QPushButton
# returns a button with specified text, icon, hint and connection to the specified function
def makeButtonBlock(parent, buttonFunction, text=None, icon=None, hint=None, name=None):
    from PyQt5 import QtWidgets
    if text is not None:
        button = QtWidgets.QPushButton(text, parent)
    else:

        button = QtWidgets.QPushButton(parent)
        button.setIcon(button.style().standardIcon(getattr(QtWidgets.QStyle, icon)))
    if hint is not None:
        button.setToolTip(hint)
        button.setToolTipDuration(2000)
    if name is not None:
        button.setObjectName(name)
    button.clicked.connect(lambda: parent.onClick(buttonFunction))


    return button
