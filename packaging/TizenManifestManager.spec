#
# spec file for package obs-service-tar_scm
#
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Patch0:         add_gbp_service.patch
#
# spec file for package obs-service-tar_scm
#
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define service gbp_git

Name:           TizenManifestManager
Version:        0.1
Release:        1
Summary:        An OBS source service: checkout or update a tar ball from git by gbp.
License:        GPL-2.0+
Group:          Development/Tools/Building
Url:            https://github.com/ronan22/TizenManifestManager
Source:         %{name}-%{version}.tar.gz

BuildRequires:  bzr
BuildRequires:  git
BuildRequires:  python >= 2.6

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

Requires:	%{service} 
Requires:	osc 

%description 
This is a source service for openSUSE Build Service.

It supports downloading from git repositories by gbp.



%package -n %{service}
Summary:        An OBS source service: checkout or update a tar ball from git by gbp.
Group:          Development/Tools/Building
Requires:       bzr
Requires:       git
Requires:       git-buildpackage-rpm

%description -n %{service}
This is a source service for openSUSE Build Service.

It supports downloading from git repositories by gbp.



%prep
%setup -q
 
%build

%install
mkdir -p %{buildroot}%{_bindir}
cp create_package_from_manifest.py %{buildroot}%{_bindir}
ln -s create_package_from_manifest.py %{buildroot}%{_bindir}/create_package_from_manifest

cp download_manifest.py  %{buildroot}%{_bindir}
ln -s download_manifest.py %{buildroot}%{_bindir}/download_manifest

cp find_spec_file.py  %{buildroot}%{_bindir}
ln -s find_spec_file.py %{buildroot}%{_bindir}/find_spec_file

cp update_project %{buildroot}%{_bindir}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 update_project.conf %{buildroot}%{_sysconfdir}/%{name}

cp update_project_manager.py %{buildroot}%{_bindir}
ln -s update_project_manager.py %{buildroot}%{_bindir}/update_project_manager

mkdir -p %{buildroot}%{_prefix}/lib/obs/service
install -m 0755 %{service} %{buildroot}%{_prefix}/lib/obs/service
install -m 0644 %{service}.service %{buildroot}%{_prefix}/lib/obs/service

mkdir -p %{buildroot}%{_sysconfdir}/obs/services
install -m 0644 %{service}.conf %{buildroot}%{_sysconfdir}/obs/services/%{service}

%files -n %{service}
%defattr(-,root,root)
%{_bindir}/create_package_from_manifest
%{_bindir}/create_package_from_manifest.py

%{_bindir}/download_manifest
%{_bindir}/download_manifest.py

%{_bindir}/find_spec_file
%{_bindir}/find_spec_file.py

%{_bindir}/update_project

%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/update_project.conf

%{_bindir}/update_project_manager
%{_bindir}/update_project_manager.py



%files -n %{service}
%defattr(-,root,root)
%dir %{_prefix}/lib/obs
%{_prefix}/lib/obs/service
%dir %{_sysconfdir}/obs
%dir %{_sysconfdir}/obs/services
%config(noreplace) %{_sysconfdir}/obs/services/*

%changelog
