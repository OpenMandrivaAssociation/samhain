%define package_version %{version}

Name:           samhain
Version:        2.5.0
Release:        %mkrel 1
Epoch:          0
Summary:        File integrity and host-based IDS
License:        GPLv2+
Group:          System/Servers
URL:            http://www.la-samhna.de/samhain/
Source0:        http://www.la-samhna.de/samhain/samhain-current.tar.gz
#Requires(post): lsb-core
#Requires(preun): lsb-core
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:  attr-devel
BuildRequires:  ext2fs-devel
BuildRequires:  gmp-devel
BuildRequires:  prelude-devel
BuildRequires:  wrap-devel
BuildRequires:  procps
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
samhain is an open source file integrity and host-based intrusion
detection system for Linux and Unix. It can run as a daemon process, and
thus can remember file changes. Contrary to a tool that runs from
cron, if a file is modified you will get only one report, while
subsequent checks of that file will ignore the modification as it is
already reported (unless the file is modified again).

samhain can optionally be used as client/server system to provide
centralized monitoring for multiple host. Logging to a (MySQL or
PostgreSQL) database is supported.

This package contains only the single host version. It also contains
support for tcp-wrappers and prelude.

This package does not contain database support.

%prep
%setup -q -c
%{__tar} xf samhain-%{package_version}.tar.gz
cd samhain-%{package_version}

%build
cd samhain-%{package_version}
%{serverbuild}
# XXX: Wow, these guys are evil, overriding the default configure
# XXX: args parsing...
./configure \
            --build=%{_target_platform} \
            --prefix=%{_prefix} \
            --exec-prefix=%{_exec_prefix} \
            --sbindir=%{_sbindir} \
            --sysconfdir=%{_sysconfdir} \
            --localstatedir=%{_var} \
            --mandir=%{_mandir} \
            --with-libwrap \
            --with-prelude
# XXX: parallel make doesn't work since `encode' must exist first
%{__make}

%install
%{__rm} -rf %{buildroot}

cd samhain-%{package_version}
%{__cat} > sstrip << EOF
#!/bin/sh
echo "*** sstrip DISABLED ***"
EOF
%{__chmod} 0755 sstrip
%{makeinstall_std}
%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 0755 init/samhain.startLSB %{buildroot}%{_initrddir}/%{name}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cat} > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
%{_logdir}/%{name}_log {
    notifempty
    missingok
    rotate 7
    daily
    compress
    create 644 root root
    postrotate
        /sbin/service %{name} reload 2>/dev/null || true
    endscript
}
EOF
/bin/touch %{buildroot}%{_logdir}/%{name}_log.lock
/bin/touch %{buildroot}%{_logdir}/%{name}_log
/bin/touch %{buildroot}%{_localstatedir}/lib/%{name}/samhain_file
/bin/touch %{buildroot}%{_localstatedir}/lib/%{name}/samhain.html

%clean
%{__rm} -rf %{buildroot}

%post
if [ "$1" = 1 ]; then
    %create_ghostfile %{_logdir}/%{name}_log.lock root root 0644
    %create_ghostfile %{_logdir}/%{name}_log root root 0644
    %create_ghostfile %{_localstatedir}/lib/%{name}/samhain_file root root 0644
    %create_ghostfile %{_localstatedir}/lib/%{name}/samhain.html root root 0644
    %{_sbindir}/samhain -t init >/dev/null 2>&1
fi
%_post_service %{name}

%preun
%_preun_service %{name}

%files
%defattr(0644,root,root,0755)
%doc samhain-%{package_version}/docs/BUGS samhain-%{package_version}/COPYING
%doc samhain-%{package_version}/docs/Changelog samhain-%{package_version}/docs/TODO
%doc samhain-%{package_version}/LICENSE samhain-%{package_version}/docs/HOWTO*
%doc samhain-%{package_version}/docs/MANUAL-* samhain-%{package_version}/docs/README*
%doc samhain-%{version}.tar.gz.asc
%attr(0755,root,root) %{_sbindir}/%{name}
%{_mandir}/man5/samhain*
%{_mandir}/man8/samhain*
%config(noreplace) %{_sysconfdir}/samhainrc
%attr(0755,root,root) %{_initrddir}/%{name}
%ghost %{_logdir}/%{name}_log
%ghost %{_logdir}/%{name}_log.lock
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_localstatedir}/lib/%{name}
%ghost %{_localstatedir}/lib/%{name}/samhain_file
%ghost %{_localstatedir}/lib/%{name}/samhain.html
