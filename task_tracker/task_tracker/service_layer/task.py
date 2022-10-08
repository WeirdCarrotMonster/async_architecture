from task_tracker.service_layer.unit_of_work import AbstractUnitOfWork

from task_tracker.domain import model, event


async def create_task(uow: AbstractUnitOfWork, description: str) -> model.Task:
    user = await uow.users.get_random_user(
        roles=[model.UserRole.manager, model.UserRole.accountant]
    )
    assert user is not None

    create_request = model.CreateTaskRequest(
        user_id=user.public_id, description=description
    )
    task = await uow.tasks.create_task(create_request)

    task_event = event.TaskAdded(
        description=task.description,
        public_id=task.public_id,
        status=task.status,
        user_id=task.user_id,
    )
    uow.events.append(task_event)

    await uow.commit()
    return task
