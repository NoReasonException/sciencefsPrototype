export PATH=$(find ~/package_manager/spack/opt/spack/linux-rhel6-x86_64/gcc-4.4.7/ -name "*" | grep "opt/spack/linux-rhel6-x86_64/gcc-4.4.7/.*/bin/*" | tr "\n" ":"):$PATH
#alias c=clear
alias activate='source ~/pyenv/bin/activate'
alias spack='~/package_manager/spack/bin/spack'
#export PATH=~/spack/opt/spack/linux-rhel6-x86_64/gcc-4.4.7/gcc-8.3.0-iiq65vau7swj4ttiochry5o4ptgh2too/bin:$PATH

