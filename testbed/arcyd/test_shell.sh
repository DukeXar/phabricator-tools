###############################################################################
# test shell for Arcyd, aimed at letting you poke around interactively
###############################################################################

set +x
set -e
trap "echo FAILED!; exit 1" EXIT

# cd to the dir of this script, so paths are relative
cd "$(dirname "$0")"

pokeloop="$(pwd)/poke_loop.sh"
arcyd="$(pwd)/../../proto/arcyd"
arcyon="$(pwd)/../../bin/arcyon"

phaburi="http://127.0.0.1"
arcyduser='phab'
arcydcert=xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrv\
afgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w\
6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk\
3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf

arcyoncreds="--uri ${phaburi} --user ${arcyduser} --cert ${arcydcert}"

tempdir=$(mktemp -d)
olddir=$(pwd)
cd ${tempdir}

mail="${olddir}/savemail"
touch savemail.txt

mkdir origin
cd origin
git init --bare
mv hooks/post-update.sample hooks/post-update
cd ..

git init --bare origin2

git clone origin dev
cd dev
git config user.name 'Bob User'
git config user.email 'bob@server.test'

echo 'feature=$(tr -dc "[:alpha:]" < /dev/urandom | head -c 8)' >> poke.sh
echo 'branch="arcyd-review/${feature}/master"' >> poke.sh
echo 'echo poke feature ${feature}' >> poke.sh
echo 'git checkout -b ${branch} origin/master' >> poke.sh
echo 'touch ${feature}' >> poke.sh
echo 'git add .' >> poke.sh
echo 'git commit -am "poked feature ${feature}"' >> poke.sh
echo 'git push -u origin ${branch}' >> poke.sh

echo "arcyon='${arcyon}'" >> accept.sh
echo "arcyoncreds='${arcyoncreds}'" >> accept.sh
echo 'revisionid=$(${arcyon} query --max-results 1 --statuses "Needs Review" --format-type ids ${arcyoncreds})' >> accept.sh
echo 'if [ -n "$revisionid" ]; then' >> accept.sh
echo '${arcyon} comment ${revisionid} --action accept ${arcyoncreds}' >> accept.sh
echo 'fi' >> accept.sh

echo "arcyd='${arcyd}'" > kill_arcyd.sh
echo 'cd ..' >> kill_arcyd.sh
echo 'arcyd_pid=$(cat arcyd.pid)' >> kill_arcyd.sh
echo 'touch killfile' >> kill_arcyd.sh
echo 'rm arcyd.pid' >> kill_arcyd.sh

echo "arcyd='${arcyd}'" > start_arcyd.sh
echo 'cd ..' >> start_arcyd.sh
echo '${arcyd} \' >> start_arcyd.sh
    echo 'process-repos \' >> start_arcyd.sh
    echo '--sys-admin-emails admin@server.test \' >> start_arcyd.sh
    echo "--sendmail-binary '${mail}' \\" >> start_arcyd.sh
    echo '--sendmail-type catchmail \' >> start_arcyd.sh
    echo '--repo-configs @repo_arcyd.cfg \' >> start_arcyd.sh
    echo '--status-path arcyd_status.json \' >> start_arcyd.sh
    echo '--kill-file killfile \' >> start_arcyd.sh
    echo '--sleep-secs 1 \' >> start_arcyd.sh
    echo '< /dev/null > /dev/null \' >> start_arcyd.sh
echo '&' >> start_arcyd.sh
echo 'arcyd_pid=$!' >> start_arcyd.sh
echo 'echo ${arcyd_pid} > arcyd.pid' >> start_arcyd.sh

chmod +x poke.sh
chmod +x accept.sh
chmod +x kill_arcyd.sh
chmod +x start_arcyd.sh

git add .
git commit -m 'intial commit'
git push origin master
cd ..

git clone origin2 dev2
cd dev2
git config user.name 'Unseen User'
git config user.email 'unseen@server.test'

touch README
git add README

git commit -m 'intial commit'
git push origin master
cd ..

git clone origin arcyd
git clone origin2 arcyd2

mkdir -p touches

touch repo_arcyd.cfg
echo @instance_local.cfg >> repo_arcyd.cfg
echo @email_arcyd.cfg >> repo_arcyd.cfg
echo @email_admin.cfg >> repo_arcyd.cfg
echo --repo-desc >> repo_arcyd.cfg
echo arcyd test >> repo_arcyd.cfg
echo --repo-path >> repo_arcyd.cfg
echo arcyd >> repo_arcyd.cfg
echo --try-touch-path >> repo_arcyd.cfg
echo touches/repo_arcyd.cfg.try >> repo_arcyd.cfg
echo --ok-touch-path >> repo_arcyd.cfg
echo touches/repo_arcyd.cfg.ok >> repo_arcyd.cfg
echo --review-url-format >> repo_arcyd.cfg
echo 'http://127.0.0.1/D{review}' >> repo_arcyd.cfg
# echo --branch-url-format >> repo_arcyd.cfg
# echo 'http://my.git/gitweb?p=r.git;a=log;h=refs/heads/{branch}' >> repo_arcyd.cfg
echo --repo-snoop-url >> repo_arcyd.cfg
echo 'http://localhost:8000/info/refs' >> repo_arcyd.cfg

touch repo_arcyd2.cfg
echo @instance_local.cfg >> repo_arcyd2.cfg
echo @email_arcyd.cfg >> repo_arcyd2.cfg
echo @email_admin.cfg >> repo_arcyd2.cfg
echo --repo-desc >> repo_arcyd2.cfg
echo arcyd2 test >> repo_arcyd2.cfg
echo --repo-path >> repo_arcyd2.cfg
echo arcyd2 >> repo_arcyd2.cfg
echo --try-touch-path >> repo_arcyd2.cfg
echo touches/repo_arcyd2.cfg.try >> repo_arcyd2.cfg
echo --ok-touch-path >> repo_arcyd2.cfg
echo touches/repo_arcyd2.cfg.ok >> repo_arcyd2.cfg
echo --review-url-format >> repo_arcyd2.cfg
echo 'http://127.0.0.1/D{review}' >> repo_arcyd2.cfg

touch instance_local.cfg
echo --instance-uri >> instance_local.cfg
echo http://127.0.0.1/api/ >> instance_local.cfg
echo --arcyd-user >> instance_local.cfg
echo phab >> instance_local.cfg
echo --arcyd-cert >> instance_local.cfg
echo xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzqu\
zl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcseh\
s2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3u\
vot7fxrotwpi3ty2b2sa2kvlpf >> instance_local.cfg

touch email_arcyd.cfg
echo --arcyd-email >> email_arcyd.cfg
echo phab-role-account@server.example >> email_arcyd.cfg
echo --admin-email >> email_admin.cfg
echo admin@server.example >> email_admin.cfg

echo 'press enter to stop.'

# run an http server for Git in the background, for snooping
cd origin
    python -m SimpleHTTPServer 8000 < /dev/null > webserver.log 2>&1 &
    webserver_pid=$!
cd -

# run arcyd instaweb in the background
${arcyd} \
    instaweb \
    --report-file arcyd_status.json \
    --repo-file-dir touches \
    --port 8001 \
&
instaweb_pid=$!

# run arcyd in the background
${arcyd} \
    process-repos \
    --sys-admin-emails admin@server.test \
    --sendmail-binary ${mail} \
    --sendmail-type catchmail \
    --repo-configs @repo_arcyd.cfg \
    --repo-configs @repo_arcyd2.cfg \
    --status-path arcyd_status.json \
    --kill-file killfile \
    --io-log-file arcyd-io.log \
    --sleep-secs 1 \
    < /dev/null > /dev/null \
&
arcyd_pid=$!

echo ${arcyd_pid} > arcyd.pid

function cleanup() {

    set +e

    echo $instaweb_pid
    kill $instaweb_pid
    wait $instaweb_pid

    arcyd_pid=$(cat arcyd.pid)

    # kill arycd
    touch killfile
    wait $arcyd_pid

    echo $webserver_pid
    kill $webserver_pid
    wait $webserver_pid

    # display the sent mails
    pwd
    cat savemail.txt

    # clean up
    cd ${olddir}
    rm -rf ${tempdir}

    echo finished.
}

trap cleanup EXIT
cd dev
    /usr/bin/env bash
cd -
trap - EXIT
cleanup
#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
