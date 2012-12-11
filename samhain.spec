%define package_version %{version}

Name:           samhain
Version:        2.5.2b
Release:        %mkrel 2
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
%setup_compile_flags
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


%changelog
* Sun May 17 2009 Funda Wang <fundawang@mandriva.org> 0:2.5.2b-2mdv2010.0
+ Revision: 376586
- use configure flags

* Mon Feb 02 2009 Jérôme Soyer <saispo@mandriva.org> 0:2.5.2b-1mdv2009.1
+ Revision: 336529
- New upstream release

* Mon Jan 12 2009 Jérôme Soyer <saispo@mandriva.org> 0:2.5.1-1mdv2009.1
+ Revision: 328658
- New upstream release

* Wed Nov 05 2008 David Walluck <walluck@mandriva.org> 0:2.5.0-1mdv2009.1
+ Revision: 300072
- 2.5.0

* Thu Sep 04 2008 Jérôme Soyer <saispo@mandriva.org> 0:2.4.6-1mdv2009.0
+ Revision: 280660
- New release

* Tue Aug 19 2008 David Walluck <walluck@mandriva.org> 0:2.4.5-1mdv2009.0
+ Revision: 273495
- 2.4.5a

* Fri Aug 08 2008 Thierry Vignaud <tvignaud@mandriva.com> 0:2.4.4-2mdv2009.0
+ Revision: 269240
- rebuild early 2009.0 package (before pixel changes)

* Tue May 06 2008 David Walluck <walluck@mandriva.org> 0:2.4.4-1mdv2009.0
+ Revision: 201741
- 2.4.4

* Wed Feb 06 2008 David Walluck <walluck@mandriva.org> 0:2.4.3-1mdv2008.1
+ Revision: 163195
- 2.4.3

* Thu Jan 24 2008 Funda Wang <fundawang@mandriva.org> 0:2.4.2-2mdv2008.1
+ Revision: 157297
- rebuild

  + David Walluck <walluck@mandriva.org>
    - 2.4.2
    - don't require lsb-core
    - silence samhain output in %%post

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tvignaud@mandriva.com>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Nov 27 2007 David Walluck <walluck@mandriva.org> 0:2.4.1-1mdv2008.1
+ Revision: 113292
- 2.4.1

* Fri Nov 02 2007 David Walluck <walluck@mandriva.org> 0:2.4.0-1mdv2008.1
+ Revision: 104875
- 2.4.0

* Thu Oct 11 2007 David Walluck <walluck@mandriva.org> 0:2.3.8-1mdv2008.1
+ Revision: 97057
- 2.3.8
- 2.3.7
- 2.3.6
- fix BuildRequires

* Sat Jun 23 2007 David Walluck <walluck@mandriva.org> 0:2.3.5-2mdv2008.0
+ Revision: 43520
- disable parallel make
- add some BuildRequires
- 2.3.5

* Thu May 03 2007 David Walluck <walluck@mandriva.org> 0:2.3.4-1mdv2008.0
+ Revision: 20828
- 2.3.4


* Wed Apr 04 2007 David Walluck <walluck@mandriva.org> 2.3.3-1mdv2007.1
+ Revision: 150463
- 2.3.3

* Wed Feb 07 2007 David Walluck <walluck@mandriva.org> 0:2.3.2-1mdv2007.1
+ Revision: 116957
- 2.3.2

* Thu Jan 25 2007 David Walluck <walluck@mandriva.org> 0:2.3.1-1mdv2007.1
+ Revision: 113072
- 2.3.1a
  fix localstatedir by setting it to %%{_var}

* Thu Nov 02 2006 David Walluck <walluck@mandriva.org> 0:2.3.0-1mdv2007.1
+ Revision: 75107
- 2.3.0a

* Sat Oct 21 2006 David Walluck <walluck@mandriva.org> 0:2.2.5-2mdv2007.0
+ Revision: 71517
- fix release tag
- rebuild
- Import samhain

* Fri Oct 20 2006 David Walluck <walluck@mandriva.org> 0:2.2.5-1
- release

