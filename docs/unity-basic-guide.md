# Unity 기초 가이드

## Unity란?

Unity는 2D와 3D 게임, 시뮬레이션, 인터랙티브 콘텐츠를 만들 수 있는 게임 엔진입니다. 개발자는 Unity Editor에서 씬을 구성하고, C# 스크립트를 작성해 오브젝트의 동작을 제어합니다.

## Hierarchy 창

Hierarchy 창은 현재 씬(Scene)에 존재하는 모든 GameObject를 계층 구조로 보여주는 창입니다. 사용자는 Hierarchy에서 오브젝트를 선택하거나 부모-자식 관계를 만들 수 있습니다.

예를 들어 `Player` 오브젝트 아래에 `Camera`나 `Weapon` 오브젝트를 자식으로 배치하면, 부모 오브젝트의 이동과 회전에 자식 오브젝트가 함께 영향을 받을 수 있습니다.

## GameObject

GameObject는 Unity 씬을 구성하는 기본 단위입니다. 캐릭터, 카메라, 조명, UI 버튼, 배경 오브젝트 등 대부분의 요소는 GameObject로 존재합니다.

GameObject 자체는 빈 컨테이너에 가깝고, 실제 기능은 Component를 추가해서 부여합니다.

## Component

Component는 GameObject에 기능을 추가하는 부품입니다. 대표적인 Component는 다음과 같습니다.

- Transform: 위치, 회전, 크기를 관리합니다.
- Mesh Renderer: 3D 모델을 화면에 렌더링합니다.
- Collider: 충돌 영역을 정의합니다.
- Rigidbody: 물리 엔진의 영향을 받게 합니다.
- Script: 개발자가 작성한 C# 동작 코드를 연결합니다.

Unity의 핵심 구조는 GameObject에 필요한 Component를 조합해서 원하는 기능을 만드는 방식입니다.

## Transform

Transform은 모든 GameObject가 기본으로 가지는 Component입니다. Transform은 오브젝트의 위치(Position), 회전(Rotation), 크기(Scale)를 관리합니다.

Hierarchy에서 부모-자식 관계가 있으면 자식 오브젝트의 Transform은 부모 오브젝트의 Transform 영향을 받습니다.

## Scene

Scene은 게임의 한 장면 또는 한 레벨을 의미합니다. 예를 들어 메인 메뉴, 전투 맵, 보스전 공간은 각각 별도의 Scene으로 만들 수 있습니다.

Unity Editor의 Scene View에서는 오브젝트를 배치하고, Game View에서는 실제 플레이어가 보게 될 화면을 확인합니다.

## Prefab

Prefab은 GameObject와 Component 구성을 에셋으로 저장한 재사용 가능한 템플릿입니다. 같은 적 캐릭터, 아이템, 총알, UI 요소를 여러 번 배치해야 할 때 Prefab을 사용하면 효율적입니다.

Prefab 원본을 수정하면 해당 Prefab을 기반으로 만든 여러 인스턴스에도 변경 사항을 적용할 수 있습니다.

## Script와 MonoBehaviour

Unity에서 게임 로직은 주로 C# 스크립트로 작성합니다. 대부분의 게임 오브젝트 스크립트는 `MonoBehaviour`를 상속합니다.

자주 사용하는 생명주기 메서드는 다음과 같습니다.

- `Start()`: 오브젝트가 활성화된 뒤 처음 한 번 실행됩니다.
- `Update()`: 매 프레임마다 실행됩니다.
- `FixedUpdate()`: 물리 계산 주기에 맞춰 실행됩니다.
- `OnCollisionEnter()`: 충돌이 시작될 때 실행됩니다.

예를 들어 플레이어 이동, 점프, 공격, 체력 감소 같은 동작은 Script Component로 구현할 수 있습니다.

## Rigidbody와 Collider

Rigidbody는 GameObject가 물리 엔진의 영향을 받도록 만드는 Component입니다. 중력, 힘, 속도 같은 물리 동작을 처리할 수 있습니다.

Collider는 충돌 판정을 위한 영역입니다. Rigidbody만 있고 Collider가 없으면 충돌을 제대로 감지하기 어렵습니다. 반대로 Collider만 있으면 충돌 영역은 있지만 물리 힘의 영향을 받지 않을 수 있습니다.

## Unity 기초 개발 흐름

Unity에서 간단한 게임을 만드는 흐름은 다음과 같습니다.

1. Scene을 생성합니다.
2. Hierarchy에 GameObject를 배치합니다.
3. GameObject에 필요한 Component를 추가합니다.
4. C# Script를 작성해 동작을 구현합니다.
5. Prefab으로 재사용할 오브젝트를 저장합니다.
6. Play 버튼으로 테스트합니다.
7. 문제가 있으면 Inspector에서 값이나 Component 설정을 수정합니다.

## 요약

Unity의 기본 개념은 Scene, GameObject, Component, Transform, Prefab, Script입니다. Hierarchy는 씬 안의 오브젝트 구조를 보여주고, Inspector는 선택한 오브젝트의 Component 설정을 보여줍니다. Unity 개발은 GameObject에 Component를 조합하고 Script로 동작을 작성하는 방식으로 진행됩니다.
