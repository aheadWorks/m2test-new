#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "update.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#
ARG BASE_VERSION="7.3"
FROM aheadworks/phpdev:${BASE_VERSION}

ARG MAGENTO_EDITION="community"
ARG MAGENTO_VERSION="2.3.4"

ARG WITH_SAMPLEDATA=""
ARG COMPOSER_AUTH

# Install cron
ADD assets/crontab /crontab
RUN crontab /crontab

COPY assets/create-install-dump.sh /tmp/create-install-dump.sh
ADD patch /.patch

COPY assets/inject-ssh-keys.sh /inject-ssh-keys.sh

RUN apk add --no-cache libzip-dev
RUN apk add --no-cache zip zlib-dev
RUN docker-php-ext-install zip
RUN apk add --no-cache mariadb-client unzip openssh-server openssh-sftp-server \
    && VER=""\
    && rm -rf /var/www/html/* \
    && if [ "${MAGENTO_VERSION}" ] ; then\
        _VER="=${MAGENTO_VERSION}"; \
    fi \
    && composer create-project --repository=https://repo.magento.com/ magento/project-${MAGENTO_EDITION}-edition${_VER} /var/www/html \
    && cd /var/www/html \
    && composer config repositories.magento composer https://repo.magento.com/ \
    && chmod u+x bin/magento \
    && COMPOSER_MEMORY_LIMIT=-1  composer install \
    && python3 -c "from pathlib import Path as p; from distutils.dir_util import copy_tree; list(map(lambda x: copy_tree(str(x), '/var/www/html'), [x for x in p('/.patch').glob('*') if str(x.name) == '${MAGENTO_VERSION}']))" \
    && if [ "$WITH_SAMPLEDATA" ] ; then \
        mkdir -p /var/www/html/var/composer_home \
        && php -dmemory_limit=-1 /var/www/html/bin/magento sampledata:deploy; \
    fi \
    && apk --no-cache add --virtual .mysql mysql \
    && sh /tmp/create-install-dump.sh \
    && rm /tmp/create-install-dump.sh \
    && rm -rf /.patch \
    && mkdir /run/sshd \
    && sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config \
    && sed -i s/AllowTcpForwarding.*/AllowTcpForwarding\ yes/ /etc/ssh/sshd_config \
    && apk del .mysql \
    && composer clearcache \
    && rm -rf /var/lib/mysql \
    && mkdir ~/.ssh

RUN ssh-keygen -A



RUN echo "http://dl-4.alpinelinux.org/alpine/v3.4/main" >> /etc/apk/repositories && \
	echo "http://dl-4.alpinelinux.org/alpine/v3.4/community" >> /etc/apk/repositories
RUN apk update

RUN apk add --update \
  openjdk11 \
  nodejs \
  nodejs-npm \
  curl \
  sudo

RUN node --version
RUN npm --version

RUN addgroup -g 1000 node \
    && adduser -u 1000 -G node -s /bin/sh -D node
RUN echo 'node ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

WORKDIR /home/node
COPY package.json .
RUN mkdir node_modules
RUN chown node:node -R .
RUN chmod 777 -R .

RUN ls -al .

USER node
RUN npm install
RUN ls -al ./node_modules/selenium-standalone/
RUN ls -al ./node_modules/selenium-standalone/.selenium


COPY assets/nginx.conf /etc/nginx/conf.d/default.conf
COPY permissions.py /permissions.py

COPY assets/entrypoint.py /entrypoint.py

USER root
ENTRYPOINT ["/usr/bin/python3", "/entrypoint.py"]
CMD ["update_and_serve"]


