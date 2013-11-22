%define service gbp_git

Name:           TizenManifestManager
Version:        0.1
Release:        1
Summary:        An OBS source service: checkout or update a tar ball from git by gbp
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
Summary:        An OBS source service: checkout or update a tar ball from git by gbp
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

cp download_manifest.py  %{buildroot}%{_bindir}
ln -s download_manifest.py %{buildroot}%{_bindir}/download_manifest

cp find_spec_file.py  %{buildroot}%{_bindir}
ln -s find_spec_file.py %{buildroot}%{_bindir}/find_spec_file

cp update_project %{buildroot}%{_bindir}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -m 0666 update_project.conf %{buildroot}%{_sysconfdir}/%{name}

cp update_project_manager.py %{buildroot}%{_bindir}
ln -s update_project_manager.py %{buildroot}%{_bindir}/update_project_manager

mkdir -p %{buildroot}%{_prefix}/lib/obs/service
install -m 0755 %{service} %{buildroot}%{_prefix}/lib/obs/service
install -m 0644 %{service}.service %{buildroot}%{_prefix}/lib/obs/service

mkdir -p %{buildroot}%{_sysconfdir}/obs/services
install -m 0644 %{service}.conf %{buildroot}%{_sysconfdir}/obs/services/%{service}

%files
%defattr(-,root,root)

%{_bindir}/download_manifest
%{_bindir}/download_manifest.py

%{_bindir}/find_spec_file
%{_bindir}/find_spec_file.py

%{_bindir}/update_project

%dir %{_sysconfdir}/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/%{name}/update_project.conf
 
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
