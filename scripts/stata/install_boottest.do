* Install boottest for wild cluster bootstrap
cap which boottest
if _rc != 0 {
    ssc install boottest, replace
    di "boottest installed successfully"
}
else {
    di "boottest already installed"
}
